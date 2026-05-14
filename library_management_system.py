# Library Management System - DSA Minor Project
# 5 DSAs: Hash Map + Trie + Queue + Heap + File I/O

from collections import deque
from datetime import datetime, timedelta
import heapq
import json
import os

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.isbn_list = []

class Book:
    def __init__(self, isbn, title, author):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.is_available = True
        self.waitlist = deque()
        self.due_date = None
        self.issue_count = 0
    
    def to_dict(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "is_available": self.is_available,
            "waitlist": list(self.waitlist),
            "due_date": self.due_date,
            "issue_count": self.issue_count
        }
    
    @staticmethod
    def from_dict(data):
        book = Book(data["isbn"], data["title"], data["author"])
        book.is_available = data["is_available"]
        book.waitlist = deque(data["waitlist"])
        book.due_date = data["due_date"]
        book.issue_count = data["issue_count"]
        return book

class Library:
    def __init__(self):
        self.books = {}
        self.title_trie = TrieNode()
        self.data_file = "library_data.json"
        self.load_library()
        
        if not self.books:
            print("Library System Initialized - New Library")
        else:
            print(f"Library System Loaded - {len(self.books)} books found")
    
    def _insert_title_to_trie(self, title, isbn):
        node = self.title_trie
        for char in title.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.isbn_list.append(isbn)
        node.is_end_of_word = True
    
    def add_book(self, isbn, title, author):
        if isbn in self.books:
            print(f"Book with ISBN {isbn} already exists")
            return
        book = Book(isbn, title, author)
        self.books[isbn] = book
        self._insert_title_to_trie(title, isbn)
        self.save_library()
        print(f"Added: {title} by {author}")
    
    def issue_book(self, isbn, user_id):
        book = self.books.get(isbn)
        if not book:
            print("Book not found")
            return
        
        if book.is_available:
            book.is_available = False
            book.issue_count += 1
            book.due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            print(f"Issued '{book.title}' to {user_id}. Due: {book.due_date}")
        else:
            book.waitlist.append(user_id)
            print(f"Book issued. {user_id} added to waitlist. Position: {len(book.waitlist)}")
        self.save_library()
    
    def return_book(self, isbn):
        book = self.books.get(isbn)
        if not book or book.is_available:
            print("Book not issued or doesn't exist")
            return
        
        print(f"Returned: {book.title}")
        if book.waitlist:
            next_user = book.waitlist.popleft()
            book.issue_count += 1
            book.due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            print(f"Auto-issued to next in queue: {next_user}. Due: {book.due_date}")
        else:
            book.is_available = True
            book.due_date = None
            print("Book is now available")
        self.save_library()
    
    def get_most_popular_books(self, top_k=5):
        if not self.books:
            print("No books in library")
            return
        
        heap = [(-book.issue_count, book.title, book.author) for book in self.books.values()]
        heapq.heapify(heap)
        
        print(f"\n--- Top {top_k} Most Popular Books ---")
        for i in range(min(top_k, len(heap))):
            count, title, author = heapq.heappop(heap)
            print(f"{i+1}. {title} by {author} | Issued {-count} times")
    
    def save_library(self):
        data = {isbn: book.to_dict() for isbn, book in self.books.items()}
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_library(self):
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            for isbn, book_data in data.items():
                book = Book.from_dict(book_data)
                self.books[isbn] = book
                self._insert_title_to_trie(book.title, isbn)

if __name__ == "__main__":
    lib = Library()
    
    if not lib.books:
        lib.add_book("978-0439709234", "Harry Potter", "J.K. Rowling")
        lib.add_book("978-0131103627", "The C Programming Language", "Dennis Ritchie")
        lib.add_book("978-0439139601", "Harry Potter 2", "J.K. Rowling")
    
    print("\n--- Testing Persistence ---")
    lib.issue_book("978-0439709234", "User1")
    lib.get_most_popular_books(top_k=3)
    
    print("\nDay 5 Complete: File I/O working ✅")
    print("Close VS Code and run again - your data will persist!")