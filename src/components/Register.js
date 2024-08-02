import React, { useState } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import './Form.css';

const Register = () => {
    const { t } = useTranslation();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/register', {
                username,
                email,
                password
            });
            setMessage(response.data.message);
        } catch (error) {
            setMessage(error.response.data.message || t('error.register'));
        }
    };

    return (
        <div className="form-container">
            <h2>{t('register')}</h2>
            <form onSubmit={handleRegister}>
                <input
                    type="text"
                    placeholder={t('username')}
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="email"
                    placeholder={t('email')}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder={t('password')}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">{t('register')}</button>
            </form>
            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default Register;
