package com.aivle.bookapp.service;

import com.aivle.bookapp.domain.Book;
import com.aivle.bookapp.dto.BookCreateRequest;
import com.aivle.bookapp.dto.BookResponse;
import com.aivle.bookapp.dto.BookUpdateRequest;
import com.aivle.bookapp.exception.BookNotFoundException;
import com.aivle.bookapp.repository.BookRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class BookService {

    private final BookRepository bookRepository;

    @Transactional(readOnly = true)
    public List<BookResponse> findAll() {
        return bookRepository.findAll().stream()
                .map(BookResponse::from)
                .toList();
    }

    @Transactional(readOnly = true)
    public BookResponse findById(Long id) {
        return BookResponse.from(getBookOrThrow(id));
    }

    @Transactional
    public BookResponse create(BookCreateRequest request) {
        Book book = Book.builder()
                .title(request.title())
                .author(request.author())
                .content(request.content())
                .build();
        return BookResponse.from(bookRepository.save(book));
    }

    @Transactional
    public BookResponse update(Long id, BookUpdateRequest request) {
        Book book = getBookOrThrow(id);

        if (request.title() != null) book.setTitle(request.title());
        if (request.author() != null) book.setAuthor(request.author());
        if (request.content() != null) book.setContent(request.content());

        return BookResponse.from(bookRepository.save(book));
    }

    @Transactional
    public BookResponse updateCover(Long id, String coverImageUrl) {
        Book book = getBookOrThrow(id);
        book.setCoverImageUrl(coverImageUrl);
        return BookResponse.from(bookRepository.save(book));
    }

    @Transactional
    public void delete(Long id) {
        if (!bookRepository.existsById(id)) {
            throw new BookNotFoundException(id);
        }
        bookRepository.deleteById(id);
    }

    // 조회 + 미존재 시 예외 처리 공통 로직
    private Book getBookOrThrow(Long id) {
        return bookRepository.findById(id)
                .orElseThrow(() -> new BookNotFoundException(id));
    }
}
