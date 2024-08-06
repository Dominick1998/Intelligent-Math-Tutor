import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const Notifications = () => {
    const { t } = useTranslation();
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        const fetchNotifications = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await axios.get('http://localhost:5000/notifications', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setNotifications(response.data);
            } catch (error) {
                console.error('Error fetching notifications', error);
            }
        };

        fetchNotifications();
    }, []);

    const markAsRead = async (id) => {
        const token = localStorage.getItem('access_token');
        try {
            await axios.post(`http://localhost:5000/notifications/read/${id}`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setNotifications(notifications.map(n => n.id === id ? { ...n, is_read: true } : n));
        } catch (error) {
            console.error('Error marking notification as read', error);
        }
    };

    return (
        <div>
            <h2>{t('notifications')}</h2>
            <ul>
                {notifications.map((notification, index) => (
                    <li key={index} style={{ background: notification.is_read ? '#e0e0e0' : '#ffffff' }}>
                        <p>{notification.message}</p>
                        <small>{new Date(notification.date_sent).toLocaleDateString()}</small>
                        {!notification.is_read && <button onClick={() => markAsRead(notification.id)}>{t('mark_as_read')}</button>}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Notifications;
