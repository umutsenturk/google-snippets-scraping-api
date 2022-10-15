#!/usr/bin/env python3

async def get_results(google_search):

    results = [
        {
            "main_search_line": "How to learn Python?",
            "parent_search_line": None,
            "snippet": "Learn Python with FreeCodeCamp...",
            "url": "https://www.freecodecamp.org/news/freecodecamp-python-courses-ranked-from-best-to-worst/"
        },
        {
            "main_search_line": "Can I teach myself Python?",
            "parent_search_line": "How to learn Python?",
            "snippet": "Can I learn Python on my own? Yes, it's totally possible to teach yourself Python. You'll find a variety of resources, from YouTube videos to books to interactive games, that can help you develop your coding skills.",
            "url": "https://www.coursera.org/articles/how-long-does-it-take-to-learn-python-tips-for-learning"
        },
        {
            "main_search_line": "How should I begin learning Python?",
            "parent_search_line": "How to learn Python?",
            "snippet": "11 Beginner Tips for Learning Python ProgrammingMake It Stick. Tip #1: Code Everyday. Tip #2: Write It Out. ...Make It Collaborative. Tip #6: Surround Yourself With Others Who Are Learning. Tip #7: Teach. ...Make Something. Tip #10: Build Something, Anything. Tip #11: Contribute to Open Source.Go Forth and Learn!",
            "url": "https://realpython.com/python-beginner-tips/"
        },
        {
            "main_search_line": "How long do it take to learn Python?",
            "parent_search_line": "How to learn Python?",
            "snippet": "If you just want to learn the Python basics, it may only take a few weeks. However, if you're pursuing a data science career from the beginning, you can expect it to take four to twelve months to learn enough advanced Python to be job-ready.",
            "url": "https://www.dataquest.io/blog/how-long-does-it-take-to-learn-python/"
        }
    ]

    return results
