package com.aivle.bookapp.controller;

import com.aivle.bookapp.domain.Book;
import com.aivle.bookapp.service.BookService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/books")
@RequiredArgsConstructor
public class BookController {

    private final BookService bookService;

    // GET /books - 목록 조회
    @GetMapping
    public ResponseEntity<List<Book>> findAll() {
        return ResponseEntity.ok(bookService.findAll());
    }

    // GET /books/{id} - 상세 조회
    @GetMapping("/{id}")
    public ResponseEntity<Book> findById(@PathVariable Long id) {
        return ResponseEntity.ok(bookService.findById(id));
    }

    // POST /books - 등록 (201 Created)
    @PostMapping
    public ResponseEntity<Book> create(@Valid @RequestBody Book book) {
        Book saved = bookService.save(book);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    // PATCH /books/{id} - 부분 수정 (title, author, content)
    @PatchMapping("/{id}")
    public ResponseEntity<Book> update(@PathVariable Long id, @RequestBody Book request) {
        return ResponseEntity.ok(bookService.update(id, request));
    }

    // PATCH /books/{id}/cover - AI 표지 URL 저장
    @PatchMapping("/{id}/cover")
    public ResponseEntity<Book> updateCover(
            @PathVariable Long id,
            @RequestBody Map<String, String> body
    ) {
        String coverImageUrl = body.get("coverImageUrl");
        return ResponseEntity.ok(bookService.updateCover(id, coverImageUrl));
    }

    // DELETE /books/{id} - 삭제 (204 No Content)
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        bookService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
