import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const Badges = () => {
    const { t } = useTranslation();
    const [badges, setBadges] = useState([]);

    useEffect(() => {
        const fetchBadges = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await axios.get('http://localhost:5000/badges', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setBadges(response.data);
            } catch (error) {
                console.error('Error fetching badges', error);
            }
        };

        fetchBadges();
    }, []);

    return (
        <div>
            <h2>{t('badges')}</h2>
            <ul>
                {badges.map((badge, index) => (
                    <li key={index}>
                        <h3>{badge.name}</h3>
                        <p>{badge.description}</p>
                        <small>{new Date(badge.date_awarded).toLocaleDateString()}</small>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Badges;
