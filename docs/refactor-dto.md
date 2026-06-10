# DTO 계층 도입 — Entity 직접 노출 제거

> 브랜치: `refactor/book-dto` (base: `fix/book-validation`)
> 검증: `mvn compile` → **BUILD SUCCESS** (JDK 17)

---

## 1. 변경 목적

### 기존 문제

Controller가 요청·응답 양쪽에서 `Book` **엔티티를 직접 사용**하고 있었다.

```java
// Before — BookController
public ResponseEntity<Book> create(@Valid @RequestBody Book book)
public ResponseEntity<Book> update(@PathVariable Long id, @RequestBody Book request)
```

여기서 발생하는 현업 관점의 문제는 세 가지다.

| # | 문제 | 설명 |
|---|------|------|
| 1 | **Mass Assignment 취약점** | 클라이언트가 `id`, `createdAt`, `updatedAt`을 요청 body에 넣어 직접 주입 가능. 서버가 관리해야 할 값을 외부가 덮어쓸 수 있음 |
| 2 | **스키마 노출** | DB 테이블 구조가 곧 API 스펙이 됨. 엔티티 필드를 바꾸면 API 응답이 그대로 깨짐 |
| 3 | **검증 책임 혼재** | 영속 모델(엔티티)에 화면 검증 규칙(`@NotBlank`)이 섞여 있어 역할이 모호 |

### 해결 방향

요청/응답 전용 **DTO(Data Transfer Object)** 를 만들어, 엔티티가 API 경계를 넘지 않도록 격리한다.

```
[Before]  Controller ⇄ Book(Entity) ⇄ Service ⇄ DB
          └ 엔티티가 외부에 그대로 노출

[After]   Controller ⇄ DTO ⇄ Service ⇄ Book(Entity) ⇄ DB
          └ 엔티티는 영속 계층 안에만 존재, 외부엔 DTO만 오감
```

---

## 2. 추가된 DTO (`com.aivle.bookapp.dto`)

모두 Java `record`로 작성 (불변 + 보일러플레이트 제거).

### BookCreateRequest — 등록 요청

```java
public record BookCreateRequest(
        @NotBlank(message = "제목은 필수입니다.")
        String title,

        String author,                      // 선택

        @NotBlank(message = "내용은 필수입니다.")
        String content
) {}
```
- 클라이언트가 보낼 수 있는 필드만 정의 → `id`/`createdAt`/`updatedAt` 주입 **원천 차단**
- 검증 규칙을 엔티티에서 이 DTO로 이동 (title·content 필수, author 선택)

### BookUpdateRequest — 부분 수정 요청

```java
public record BookUpdateRequest(
        String title,
        String author,
        String content
) {}
```
- PATCH 부분 수정용. 검증 어노테이션 없음 → 일부 필드만 전송 가능
- `null`인 필드는 Service에서 기존 값 유지

### CoverUpdateRequest — AI 표지 저장 요청

```java
public record CoverUpdateRequest(
        String coverImageUrl
) {}
```
- 기존 `Map<String, String>` 방식을 명시적 타입으로 교체 → 스펙이 코드에 드러남

### BookResponse — 응답 전용

```java
public record BookResponse(
        Long id, String title, String author, String content,
        String coverImageUrl, LocalDateTime createdAt, LocalDateTime updatedAt
) {
    public static BookResponse from(Book book) {
        return new BookResponse(
                book.getId(), book.getTitle(), book.getAuthor(),
                book.getContent(), book.getCoverImageUrl(),
                book.getCreatedAt(), book.getUpdatedAt()
        );
    }
}
```
- 모든 조회/등록/수정 응답에 사용
- `from()` 정적 팩토리로 `Book → BookResponse` 변환을 한 곳에서 관리

---

## 3. 기존 코드 변경

### Book.java (엔티티)

```diff
- import jakarta.validation.constraints.NotBlank;

- @NotBlank(message = "제목은 필수입니다.")
+ @Column(nullable = false)
  private String title;

  private String author;

- @NotBlank(message = "내용은 필수입니다.")
- @Column(columnDefinition = "TEXT")
+ @Column(columnDefinition = "TEXT", nullable = false)
  private String content;
```
- 화면 검증(`@NotBlank`)은 DTO로 이동
- 대신 `@Column(nullable = false)`로 **DB 레벨 제약**을 둬서 방어선 유지 (defense in depth)

### BookService.java

엔티티 입출력 → **DTO 입출력**으로 전환. 엔티티는 Service 내부에만 머문다.

```java
public BookResponse create(BookCreateRequest request) {
    Book book = Book.builder()
            .title(request.title())
            .author(request.author())
            .content(request.content())
            .build();
    return BookResponse.from(bookRepository.save(book));
}

public BookResponse update(Long id, BookUpdateRequest request) {
    Book book = getBookOrThrow(id);
    if (request.title() != null)   book.setTitle(request.title());
    if (request.author() != null)  book.setAuthor(request.author());
    if (request.content() != null) book.setContent(request.content());
    return BookResponse.from(bookRepository.save(book));
}

// 조회 + 미존재 예외 처리 공통화
private Book getBookOrThrow(Long id) {
    return bookRepository.findById(id)
            .orElseThrow(() -> new BookNotFoundException(id));
}
```

### BookController.java

```diff
- public ResponseEntity<Book> create(@Valid @RequestBody Book book)
+ public ResponseEntity<BookResponse> create(@Valid @RequestBody BookCreateRequest request)

- public ResponseEntity<Book> update(@PathVariable Long id, @RequestBody Book request)
+ public ResponseEntity<BookResponse> update(@PathVariable Long id, @RequestBody BookUpdateRequest request)

- @RequestBody Map<String, String> body
+ @RequestBody CoverUpdateRequest request
```
- `Book`, `Map` import 제거. 시그니처가 전부 DTO로 통일

---

## 4. 동작 영향

| 항목 | 변경 후 동작 |
|------|--------------|
| `id`/`createdAt`/`updatedAt` 주입 시도 | DTO에 해당 필드가 없어 **무시됨** (Spring Boot 기본 설정이 unknown 필드 무시). 타임스탬프는 서버 `@CreationTimestamp`/`@UpdateTimestamp`가 단독 책임 |
| `content` 누락 POST | 400 Bad Request + `{"content": "내용은 필수입니다."}` |
| `author` 누락 POST | 201 Created 정상 등록 |
| API 응답 필드 | 기존과 **동일** → 프론트엔드 수정 불필요 |
| 검증 실패 응답 | 기존 `GlobalExceptionHandler`가 `MethodArgumentNotValidException`을 그대로 처리 (변경 없음) |

---

## 5. 검증

```bash
mvn -DskipTests compile
# → [INFO] BUILD SUCCESS  (JDK 17)
```

생성 확인:
```
target/classes/com/aivle/bookapp/dto/
├── BookCreateRequest.class
├── BookUpdateRequest.class
├── CoverUpdateRequest.class
└── BookResponse.class
```

---

## 6. 변경 파일 목록

| 파일 | 상태 |
|------|------|
| `dto/BookCreateRequest.java` | 신규 |
| `dto/BookUpdateRequest.java` | 신규 |
| `dto/CoverUpdateRequest.java` | 신규 |
| `dto/BookResponse.java` | 신규 |
| `domain/Book.java` | 수정 (검증 → DB 제약) |
| `service/BookService.java` | 수정 (DTO 입출력) |
| `controller/BookController.java` | 수정 (DTO 시그니처) |
