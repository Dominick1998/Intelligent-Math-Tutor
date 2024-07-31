import React, { useState } from 'react';
import axios from 'axios';

const Feedback = () => {
    const [feedback, setFeedback] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('access_token');
        try {
            const response = await axios.post('http://localhost:5000/feedback', { feedback }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage(response.data.message);
            setFeedback('');
        } catch (error) {
            setMessage(error.response.data.message || 'Error submitting feedback');
        }
    };

    return (
        <div>
            <h2>Submit Feedback</h2>
            <form onSubmit={handleSubmit}>
                <textarea
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    placeholder="Your feedback"
                    rows="4"
                    cols="50"
                />
                <button type="submit">Submit</button>
            </form>
            <p>{message}</p>
        </div>
    );
};

export default Feedback;
