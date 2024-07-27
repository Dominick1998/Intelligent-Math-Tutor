import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
    const [data, setData] = useState({
        username: '',
        email: '',
        total_problems: 0,
        correct_answers: 0,
        incorrect_answers: 0,
        performance_ratio: 0
    });

    const [message, setMessage] = useState('');

    useEffect(() => {
        const fetchDashboard = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await axios.get('http://localhost:5000/dashboard', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setData(response.data);
            } catch (error) {
                setMessage('Error fetching dashboard data');
            }
        };

        fetchDashboard();
    }, []);

    return (
        <div>
            <h2>Dashboard</h2>
            {message ? (
                <p>{message}</p>
            ) : (
                <div>
                    <p>Username: {data.username}</p>
                    <p>Email: {data.email}</p>
                    <p>Total Problems: {data.total_problems}</p>
                    <p>Correct Answers: {data.correct_answers}</p>
                    <p>Incorrect Answers: {data.incorrect_answers}</p>
                    <p>Performance Ratio: {data.performance_ratio.toFixed(2)}</p>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
