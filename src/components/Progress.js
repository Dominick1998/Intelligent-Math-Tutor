import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Progress = ({ userId }) => {
    const [progress, setProgress] = useState([]);

    useEffect(() => {
        const fetchProgress = async () => {
            try {
                const response = await axios.get(`http://localhost:5000/progress/${userId}`);
                setProgress(response.data);
            } catch (error) {
                console.error('Error fetching progress:', error);
            }
        };

        fetchProgress();
    }, [userId]);

    return (
        <div>
            <h2>Your Progress</h2>
            <ul>
                {progress.map((entry, index) => (
                    <li key={index}>
                        Problem ID: {entry.problem_id}, Status: {entry.status}, Timestamp: {new Date(entry.timestamp).toLocaleString()}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Progress;
