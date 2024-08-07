import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const AdminPanel = () => {
    const { t } = useTranslation();
    const [users, setUsers] = useState([]);
    const [feedback, setFeedback] = useState([]);

    useEffect(() => {
        const fetchUsers = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await axios.get('http://localhost:5000/admin/users', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUsers(response.data);
            } catch (error) {
                console.error('Error fetching users', error);
            }
        };

        const fetchFeedback = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await axios.get('http://localhost:5000/admin/feedback', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setFeedback(response.data);
            } catch (error) {
                console.error('Error fetching feedback', error);
            }
        };

        fetchUsers();
        fetchFeedback();
    }, []);

    const deleteUser = async (id) => {
        const token = localStorage.getItem('access_token');
        try {
            await axios.delete(`http://localhost:5000/admin/users/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(users.filter(user => user.id !== id));
        } catch (error) {
            console.error('Error deleting user', error);
        }
    };

    return (
        <div>
            <h2>{t('admin_panel')}</h2>
            <h3>{t('users')}</h3>
            <ul>
                {users.map(user => (
                    <li key={user.id}>
                        {user.username} ({user.email})
                        <button onClick={() => deleteUser(user.id)}>{t('delete')}</button>
                    </li>
                ))}
            </ul>
            <h3>{t('feedback')}</h3>
            <ul>
                {feedback.map(f => (
                    <li key={f.id}>
                        User {f.user_id}: {f.feedback} - {new Date(f.timestamp).toLocaleDateString()}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default AdminPanel;
