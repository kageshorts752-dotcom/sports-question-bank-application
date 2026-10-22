"""Vercel serverless entry point for the Flask app.

Vercel turns every file under api/ into a serverless function. This file
imports the Flask app from the project root so all routes (/, /add, /edit,
/delete, /export, /question-set, /static/...) are served by one function.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402

# Vercel's Python runtime looks for `app` in this module.
