import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# Define the GraphQL representation of a Book using decorators
@strawberry.type
class Book:
    id: int
    title: str
    author: str
    year: int

# In-memory database representation
BOOKS_DB = [
    Book(id=1, title="1984", author="George Orwell", year=1949),
    Book(id=2, title="Dune", author="Frank Herbert", year=1965),
]

# Define queries to fetch data
@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> list[Book]:
        """Retrieve all books from the collection."""
        return BOOKS_DB

    @strawberry.field
    def book(self, id: int) -> Book | None:
        """Retrieve a specific book by its unique identifier."""
        return next((b for b in BOOKS_DB if b.id == id), None)

# Define mutations to modify data
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, id: int, title: str, author: str, year: int) -> Book:
        """Add a new book to the database."""
        new_book = Book(id=id, title=title, author=author, year=year)
        BOOKS_DB.append(new_book)
        return new_book

# Combine Query and Mutation types into a unified Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Initialise the Strawberry router and integrate it with FastAPI
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="GraphQL API")
app.include_router(graphql_app, prefix="/graphql")
