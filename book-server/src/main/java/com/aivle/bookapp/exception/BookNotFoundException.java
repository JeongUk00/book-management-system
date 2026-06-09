package com.aivle.bookapp.exception;

public class BookNotFoundException extends RuntimeException {
    public BookNotFoundException(Long id) {
        super("도서를 찾을 수 없습니다. id: " + id);
    }
}
