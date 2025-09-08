import unittest
from unittest.mock import patch, MagicMock
from your_module import generate_mongo_query_with_schema, detect_relevant_schema, classify_question

class TestMongoQueryGeneration(unittest.TestCase):
    
    def setUp(self):
        self.valid_questions = [
            "Find all active users",
            "Retrieve invoices where status is 'approved'",
            "Get schedules where the duration is more than 3 hours"
        ]
        
        self.error_questions = [
            "Find invoices where the total hours worked match the instructor’s schedule",
            "Count the number of active users",
            "Get the total number of invoices"
        ]
    
    @patch('your_module.client.chat.completions.create')
    def test_generate_mongo_query_with_schema_valid(self, mock_chat_completion):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="db.users.find({status: 'active'})"))]
        mock_chat_completion.return_value = mock_response
        
        for question in self.valid_questions:
            with self.subTest(question=question):
                query = generate_mongo_query_with_schema(question)
                self.assertIn("db.", query, f"Query not generated properly for: {question}")
    
    @patch('your_module.client.chat.completions.create')
    def test_generate_mongo_query_with_schema_error(self, mock_chat_completion):
        mock_chat_completion.side_effect = Exception("API error")
        
        for question in self.error_questions:
            with self.subTest(question=question):
                query = generate_mongo_query_with_schema(question)
                self.assertEqual(query, "Error: Unexpected error occurred.")
    
    def test_detect_relevant_schema(self):
        test_cases = {
            "Find all active users": "users",
            "Retrieve invoices where status is 'approved'": "invoices",
            "Get schedules where the duration is more than 3 hours": "schedule"
        }
        
        for question, expected in test_cases.items():
            with self.subTest(question=question):
                schema = detect_relevant_schema(question)
                self.assertIsNotNone(schema, f"Schema detection failed for: {question}")
                self.assertIn(expected, schema.lower(), f"Incorrect schema detected for: {question}")
    
    @patch('your_module.client.chat.completions.create')
    def test_classify_question(self, mock_chat_completion):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="specific"))]
        mock_chat_completion.return_value = mock_response
        
        result = classify_question("Find all active users", "users schema")
        self.assertEqual(result, "specific", "Question classification failed")
    
if __name__ == '__main__':
    unittest.main()
