"""
TASK 2: CHATBOT FOR FAQs
CodeAlpha Artificial Intelligence Internship

A chatbot that answers Frequently Asked Questions (FAQs) by matching
the user's question to the most similar FAQ using NLP preprocessing
and Cosine Similarity (TF-IDF vectorization).

Domain chosen: Online Store Customer Support FAQs

How it works:
1. Collect FAQ pairs (question + answer)
2. Preprocess text: lowercase, remove punctuation, tokenize, remove stopwords
3. Convert all questions into TF-IDF vectors
4. When user asks something, convert it to a vector too
5. Find the FAQ question with highest Cosine Similarity to user's question
6. Return that FAQ's answer
"""

import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data (only runs once)
for pkg in ["punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
    except LookupError:
        nltk.download(pkg, quiet=True)


# ── STEP 1: FAQ DATASET (Online Store Customer Support) ─────────
FAQ_DATA = [
    ("How can I track my order?",
     "You can track your order by going to 'My Orders' in your account and clicking on 'Track Order'. You will also receive a tracking link via email."),

    ("What is your return policy?",
     "We accept returns within 30 days of delivery. The item must be unused and in its original packaging. Refunds are processed within 5-7 business days."),

    ("How do I cancel my order?",
     "You can cancel your order within 1 hour of placing it by going to 'My Orders' and selecting 'Cancel Order'. After that, please contact customer support."),

    ("What payment methods do you accept?",
     "We accept credit/debit cards, PayPal, bank transfer, and cash on delivery in selected regions."),

    ("How long does delivery take?",
     "Standard delivery takes 3-5 business days. Express delivery takes 1-2 business days. International orders may take 7-14 business days."),

    ("Do you offer free shipping?",
     "Yes! We offer free shipping on all orders above $50. Orders below that amount have a flat shipping fee of $5."),

    ("How can I change my delivery address?",
     "You can change your delivery address before the order is shipped by going to 'My Orders' and selecting 'Edit Address'. Once shipped, the address cannot be changed."),

    ("What should I do if I received a damaged product?",
     "We're sorry for the inconvenience. Please contact customer support within 48 hours with photos of the damaged item, and we will arrange a replacement or refund."),

    ("How do I reset my account password?",
     "Click on 'Forgot Password' on the login page, enter your registered email, and follow the link sent to your inbox to reset your password."),

    ("Can I get an invoice for my purchase?",
     "Yes, an invoice is automatically generated and emailed to you after purchase. You can also download it from 'My Orders' > 'Invoice'."),

    ("How do I contact customer support?",
     "You can reach our customer support team via live chat on our website, email at support@store.com, or by calling our helpline at 1-800-555-0199."),

    ("Do you ship internationally?",
     "Yes, we ship to over 50 countries worldwide. International shipping rates and delivery times vary by location."),

    ("How do I apply a discount code?",
     "Enter your discount code in the 'Promo Code' box at checkout and click 'Apply'. The discount will be reflected in your total before payment."),

    ("Is my personal information secure?",
     "Yes, we use industry-standard SSL encryption to protect your personal and payment information. We never share your data with third parties without consent."),

    ("Can I exchange a product instead of returning it?",
     "Yes, exchanges are allowed within 30 days for a different size or color, subject to availability. Visit 'My Orders' > 'Exchange Item' to start the process."),
]


# ── STEP 2: TEXT PREPROCESSING (NLP) ─────────────────────────────
stop_words = set(stopwords.words("english"))

# Simple synonym map to normalize common word variations before matching
SYNONYMS = {
    "package": "order", "parcel": "order",
    "money": "return", "refund": "return", "reimburse": "return",
    "card": "payment", "cards": "payment", "pay": "payment", "paying": "payment",
    "broken": "damaged", "arrived": "received", "arrive": "received",
    "deliver": "shipping", "deliveries": "shipping",
    "countries": "internationally", "country": "internationally", "abroad": "internationally",
    "know": "track", "find": "track",
    "safe": "secure", "info": "information",
}

def expand_synonyms(tokens):
    return [SYNONYMS.get(t, t) for t in tokens]

def preprocess(text):
    """Clean text: lowercase, remove punctuation, tokenize, remove stopwords, normalize synonyms."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in stop_words and t.isalpha()]
    tokens = expand_synonyms(tokens)
    return " ".join(tokens)


# ── STEP 3: BUILD TF-IDF MODEL ───────────────────────────────────
class FAQChatbot:
    def __init__(self, faq_data):
        self.questions = [q for q, a in faq_data]
        self.answers = [a for q, a in faq_data]

        # Preprocess all FAQ questions
        self.processed_questions = [preprocess(q) for q in self.questions]

        # Build TF-IDF vectorizer on the FAQ questions
        # ngram_range=(1,2) also considers word pairs, improving match quality
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_questions)

    def get_response(self, user_input, threshold=0.12):
        """Find the most similar FAQ and return its answer."""
        processed_input = preprocess(user_input)

        if not processed_input.strip():
            return "Could you please rephrase your question?", 0.0

        # Convert user input to TF-IDF vector using same vectorizer
        user_vector = self.vectorizer.transform([processed_input])

        # Calculate cosine similarity with all FAQ questions
        similarities = cosine_similarity(user_vector, self.tfidf_matrix)[0]

        best_idx = similarities.argmax()
        best_score = similarities[best_idx]

        if best_score < threshold:
            return ("I'm sorry, I couldn't find a matching answer. "
                    "Please contact our support team at support@store.com for further help."), best_score

        return self.answers[best_idx], best_score

    def show_matched_question(self, user_input):
        """Debug helper: shows which FAQ was matched and the similarity score."""
        processed_input = preprocess(user_input)
        user_vector = self.vectorizer.transform([processed_input])
        similarities = cosine_similarity(user_vector, self.tfidf_matrix)[0]
        best_idx = similarities.argmax()
        return self.questions[best_idx], similarities[best_idx]


# ── STEP 4: CHAT LOOP (Console Interface) ────────────────────────
def run_chatbot():
    bot = FAQChatbot(FAQ_DATA)

    print("=" * 60)
    print("  🤖 FAQ CHATBOT — Online Store Customer Support")
    print("=" * 60)
    print("Ask me anything about orders, returns, shipping, payments...")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit", "bye"):
            print("Bot: Thank you for chatting with us. Goodbye! 👋")
            break

        answer, score = bot.get_response(user_input)
        print(f"Bot: {answer}")
        print(f"     (Confidence: {score:.2f})\n")


# ── STEP 5: SIMPLE GUI VERSION (Tkinter) ─────────────────────────
def run_gui():
    import tkinter as tk
    from tkinter import scrolledtext

    bot = FAQChatbot(FAQ_DATA)
    root = tk.Tk()
    root.title("FAQ Chatbot — CodeAlpha")
    root.geometry("500x600")
    root.configure(bg="#1e1e2e")

    tk.Label(root, text="🤖 FAQ Chatbot", font=("Segoe UI", 18, "bold"),
             bg="#1e1e2e", fg="#89b4fa").pack(pady=10)

    chat_box = scrolledtext.ScrolledText(
        root, wrap="word", font=("Segoe UI", 10),
        bg="#313244", fg="#cdd6f4", height=25
    )
    chat_box.pack(padx=15, pady=10, fill="both", expand=True)
    chat_box.insert(tk.END, "Bot: Hi! Ask me about orders, returns, shipping, or payments.\n\n")
    chat_box.config(state="disabled")

    entry_frame = tk.Frame(root, bg="#1e1e2e")
    entry_frame.pack(fill="x", padx=15, pady=10)

    entry = tk.Entry(entry_frame, font=("Segoe UI", 11), bg="#313244", fg="white")
    entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def send_message():
        user_text = entry.get().strip()
        if not user_text:
            return
        answer, score = bot.get_response(user_text)

        chat_box.config(state="normal")
        chat_box.insert(tk.END, f"You: {user_text}\n")
        chat_box.insert(tk.END, f"Bot: {answer}\n\n")
        chat_box.config(state="disabled")
        chat_box.see(tk.END)
        entry.delete(0, tk.END)

    send_btn = tk.Button(entry_frame, text="Send", font=("Segoe UI", 10, "bold"),
                          bg="#89b4fa", fg="#1e1e2e", command=send_message)
    send_btn.pack(side="right")
    entry.bind("<Return>", lambda e: send_message())

    root.mainloop()


if __name__ == "__main__":
    import sys
    if "--gui" in sys.argv:
        run_gui()
    else:
        run_chatbot()
