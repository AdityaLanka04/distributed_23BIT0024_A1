"""
Quiz Presets - Pre-configured quiz categories with questions
"""

QUIZ_PRESETS = {
    "english": {
        "title": "English Literature & Grammar",
        "description": "Test your knowledge of English literature, grammar, and vocabulary",
        "category": "English",
        "icon": "EN",
        "color": "#0f766e",
        "duration_minutes": 15,
        "questions": [
            {
                "question_text": "Who wrote 'Romeo and Juliet'?",
                "options": ["William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain"],
                "correct_answer": 0,
                "points": 1
            },
            {
                "question_text": "What is the past tense of 'run'?",
                "options": ["Runned", "Ran", "Running", "Runs"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "Which of these is a noun?",
                "options": ["Quickly", "Beautiful", "Happiness", "Running"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Who wrote '1984'?",
                "options": ["George Orwell", "Aldous Huxley", "Ray Bradbury", "Ernest Hemingway"],
                "correct_answer": 0,
                "points": 1
            },
            {
                "question_text": "What is a synonym for 'happy'?",
                "options": ["Sad", "Joyful", "Angry", "Tired"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "Which sentence is grammatically correct?",
                "options": ["She don't like pizza", "She doesn't likes pizza", "She doesn't like pizza", "She not like pizza"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "What literary device is used in 'The stars danced in the sky'?",
                "options": ["Simile", "Metaphor", "Personification", "Alliteration"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Who wrote 'Pride and Prejudice'?",
                "options": ["Emily Brontë", "Jane Austen", "Charlotte Brontë", "Virginia Woolf"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "What is the plural of 'child'?",
                "options": ["Childs", "Childes", "Children", "Childrens"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Which word is an adjective?",
                "options": ["Run", "Beautiful", "Quickly", "Happiness"],
                "correct_answer": 1,
                "points": 1
            }
        ]
    },
    "world_history": {
        "title": "World History",
        "description": "Journey through major events and figures in world history",
        "category": "History",
        "icon": "WH",
        "color": "#f97316",
        "duration_minutes": 15,
        "questions": [
            {
                "question_text": "In which year did World War II end?",
                "options": ["1943", "1944", "1945", "1946"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Who was the first President of the United States?",
                "options": ["Thomas Jefferson", "George Washington", "John Adams", "Benjamin Franklin"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "The French Revolution began in which year?",
                "options": ["1776", "1789", "1799", "1804"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "Who was known as the 'Iron Lady'?",
                "options": ["Margaret Thatcher", "Indira Gandhi", "Angela Merkel", "Golda Meir"],
                "correct_answer": 0,
                "points": 1
            },
            {
                "question_text": "The Berlin Wall fell in which year?",
                "options": ["1987", "1988", "1989", "1990"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Who discovered America in 1492?",
                "options": ["Vasco da Gama", "Christopher Columbus", "Ferdinand Magellan", "Marco Polo"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "The Renaissance began in which country?",
                "options": ["France", "Spain", "Italy", "England"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Who was the first man to walk on the moon?",
                "options": ["Buzz Aldrin", "Neil Armstrong", "Yuri Gagarin", "John Glenn"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "The Roman Empire fell in which century?",
                "options": ["3rd century", "4th century", "5th century", "6th century"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Who was the leader of Nazi Germany?",
                "options": ["Benito Mussolini", "Joseph Stalin", "Adolf Hitler", "Winston Churchill"],
                "correct_answer": 2,
                "points": 1
            }
        ]
    },
    "geography": {
        "title": "World Geography",
        "description": "Explore countries, continents, and geographical features",
        "category": "Geography",
        "icon": "GEO",
        "color": "#0891b2",
        "duration_minutes": 15,
        "questions": [
            {
                "question_text": "What is the largest continent by area?",
                "options": ["Africa", "Asia", "North America", "Europe"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "Which river is the longest in the world?",
                "options": ["Amazon", "Nile", "Yangtze", "Mississippi"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "Mount Everest is located in which mountain range?",
                "options": ["Alps", "Andes", "Himalayas", "Rockies"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Which is the smallest ocean?",
                "options": ["Atlantic", "Indian", "Arctic", "Southern"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "The Sahara Desert is located in which continent?",
                "options": ["Asia", "Australia", "Africa", "South America"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Which country has the most natural lakes?",
                "options": ["USA", "Canada", "Russia", "Brazil"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "The Great Barrier Reef is located off the coast of which country?",
                "options": ["Brazil", "Indonesia", "Australia", "Philippines"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Which is the driest place on Earth?",
                "options": ["Sahara Desert", "Death Valley", "Atacama Desert", "Gobi Desert"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "The Amazon Rainforest is primarily located in which country?",
                "options": ["Colombia", "Peru", "Brazil", "Venezuela"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Which line divides the Earth into Northern and Southern hemispheres?",
                "options": ["Prime Meridian", "Tropic of Cancer", "Equator", "International Date Line"],
                "correct_answer": 2,
                "points": 1
            }
        ]
    },
    "world_capitals": {
        "title": "World Capitals",
        "description": "Test your knowledge of capital cities around the world",
        "category": "Geography",
        "icon": "CAP",
        "color": "#059669",
        "duration_minutes": 15,
        "questions": [
            {
                "question_text": "What is the capital of France?",
                "options": ["London", "Paris", "Berlin", "Rome"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "What is the capital of Japan?",
                "options": ["Seoul", "Beijing", "Tokyo", "Bangkok"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "What is the capital of Australia?",
                "options": ["Sydney", "Melbourne", "Canberra", "Brisbane"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "What is the capital of Brazil?",
                "options": ["Rio de Janeiro", "São Paulo", "Brasília", "Salvador"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "What is the capital of Canada?",
                "options": ["Toronto", "Vancouver", "Montreal", "Ottawa"],
                "correct_answer": 3,
                "points": 1
            },
            {
                "question_text": "What is the capital of Egypt?",
                "options": ["Alexandria", "Cairo", "Giza", "Luxor"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "What is the capital of Spain?",
                "options": ["Barcelona", "Madrid", "Valencia", "Seville"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "What is the capital of South Korea?",
                "options": ["Busan", "Seoul", "Incheon", "Daegu"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "What is the capital of Turkey?",
                "options": ["Istanbul", "Ankara", "Izmir", "Antalya"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "What is the capital of Switzerland?",
                "options": ["Zurich", "Geneva", "Bern", "Basel"],
                "correct_answer": 2,
                "points": 1
            }
        ]
    },
    "indian_history": {
        "title": "Indian History",
        "description": "Explore the rich history and heritage of India",
        "category": "History",
        "icon": "IND",
        "color": "#ea580c",
        "duration_minutes": 15,
        "questions": [
            {
                "question_text": "Who was the first Prime Minister of India?",
                "options": ["Mahatma Gandhi", "Jawaharlal Nehru", "Sardar Patel", "Dr. Rajendra Prasad"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "In which year did India gain independence?",
                "options": ["1945", "1946", "1947", "1948"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "Who built the Taj Mahal?",
                "options": ["Akbar", "Shah Jahan", "Aurangzeb", "Jahangir"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "The Quit India Movement was launched in which year?",
                "options": ["1940", "1942", "1944", "1946"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "Who was known as the 'Iron Man of India'?",
                "options": ["Jawaharlal Nehru", "Subhas Chandra Bose", "Sardar Vallabhbhai Patel", "Bhagat Singh"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "The Battle of Plassey was fought in which year?",
                "options": ["1757", "1764", "1857", "1947"],
                "correct_answer": 0,
                "points": 1
            },
            {
                "question_text": "Who founded the Maurya Empire?",
                "options": ["Ashoka", "Chandragupta Maurya", "Bindusara", "Chanakya"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "The Indian National Congress was founded in which year?",
                "options": ["1857", "1885", "1905", "1920"],
                "correct_answer": 1,
                "points": 1
            },
            {
                "question_text": "Who gave the slogan 'Jai Hind'?",
                "options": ["Mahatma Gandhi", "Jawaharlal Nehru", "Subhas Chandra Bose", "Bhagat Singh"],
                "correct_answer": 2,
                "points": 1
            },
            {
                "question_text": "The Jallianwala Bagh massacre occurred in which city?",
                "options": ["Delhi", "Lahore", "Amritsar", "Calcutta"],
                "correct_answer": 2,
                "points": 1
            }
        ]
    }
}

def get_preset_quiz(preset_id: str):
    """Get a preset quiz by ID"""
    return QUIZ_PRESETS.get(preset_id)

def get_all_presets():
    """Get all available preset quizzes"""
    return {
        key: {
            "id": key,
            "title": value["title"],
            "description": value["description"],
            "category": value["category"],
            "icon": value["icon"],
            "color": value["color"],
            "question_count": len(value["questions"])
        }
        for key, value in QUIZ_PRESETS.items()
    }
