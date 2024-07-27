import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Profile = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');

    useEffect(() => {
        const fetchProfile = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await axios.get('http://localhost:5000/profile', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsername(response.data.username);
                setEmail(response.data.email);
            } catch (error) {
                setMessage('Error fetching profile');
            }
        };

        fetchProfile();
    }, []);

    const handleUpdate = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('access_token');
        try {
            const response = await axios.put('http://localhost:5000/profile', {
                username,
                email
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage(response.data.message);
        } catch (error) {
            setMessage('Error updating profile');
        }
    };

    return (
        <div>
            <h2>Profile</h2>
            <form onSubmit={handleUpdate}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <button type="submit">Update Profile</button>
            </form>
            <p>{message}</p>
        </div>
    );
};

export default Profile;
