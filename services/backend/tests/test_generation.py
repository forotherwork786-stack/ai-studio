import unittest

from app.queue import GenerationQueue, QueueEntry


class QueueTests(unittest.TestCase):
    def test_enqueue_and_list(self):
        queue = GenerationQueue(max_concurrency=1)
        entry = QueueEntry(task_id='t-1', task_type='image', model_name='sd15', prompt='Test prompt')
        queue.add(entry)
        self.assertEqual(len(queue.list()), 1)
        self.assertEqual(queue.get('t-1').status, 'Waiting')

    def test_cancel_and_retry(self):
        queue = GenerationQueue(max_concurrency=1)
        entry = QueueEntry(task_id='t-2', task_type='image', model_name='sd15', prompt='Test prompt', status='Generating')
        queue.add(entry)
        queue.cancel('t-2')
        self.assertEqual(queue.get('t-2').status, 'Cancelled')
        queue.retry('t-2')
        self.assertEqual(queue.get('t-2').status, 'Waiting')

    def test_can_enqueue_respects_limit(self):
        queue = GenerationQueue(max_concurrency=1)
        self.assertTrue(queue.can_enqueue())
        queue.active = 1
        self.assertFalse(queue.can_enqueue())


if __name__ == '__main__':
    unittest.main()
