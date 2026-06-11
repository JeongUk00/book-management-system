import { Link, useNavigate } from 'react-router-dom'

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export default function BookCard({ book }) {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const isLoggedIn = Boolean(localStorage.getItem('token'))
  const isOwner = user?.userId === book.ownerId

  const handleClick = (event) => {
    event.preventDefault()

    if (!isLoggedIn) {
      navigate('/login')
      return
    }

    if (!isOwner) {
      window.alert('본인이 등록한 도서만 상세 조회할 수 있습니다.')
      return
    }

    navigate(`/books/${book.id}`)
  }

  return (
    <Link to={`/books/${book.id}`} className="book-card" onClick={handleClick}>
      {book.coverImageUrl ? (
        <img
          src={book.coverImageUrl}
          alt={`${book.title} 표지`}
          className="book-card-cover"
        />
      ) : (
        <div className="book-card-cover-placeholder">
          <span className="placeholder-icon">📖</span>
          <p>표지 없음</p>
        </div>
      )}

      <div className="book-card-body">
        <p className="book-card-title">{book.title}</p>
        <p className="book-card-author">{book.author || '저자 미상'}</p>
        <p className="book-card-date">{formatDate(book.createdAt)}</p>
      </div>
    </Link>
  )
}