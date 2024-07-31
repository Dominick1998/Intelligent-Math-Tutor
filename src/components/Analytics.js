import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Analytics = () => {
    const [data, setData] = useState({});
    const [message, setMessage] = useState('');

    useEffect(() => {
        const fetchAnalytics = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await axios.get('http://localhost:5000/analytics', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setData(response.data);
            } catch (error) {
                setMessage('Error fetching analytics data');
            }
        };

        fetchAnalytics();
    }, []);

    return (
        <div>
            <h2>User Analytics</h2>
            {message ? (
                <p>{message}</p>
            ) : (
                <div>
                    <p>Username: {data.username}</p>
                    <p>Email: {data.email}</p>
                    <p>Total Problems: {data.total_problems}</p>
                    <p>Correct Answers: {data.correct_answers}</p>
                    <p>Incorrect Answers: {data.incorrect_answers}</p>
                    <p>Performance Ratio: {data.performance_ratio}</p>
                    <p>Feedback Count: {data.feedback_count}</p>
                </div>
            )}
        </div>
    );
};

export default Analytics;
