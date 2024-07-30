import React, { useState } from 'react';
import axios from 'axios';
import './Form.css';

const Login = ({ setUserId }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/login', {
                email,
                password
            });
            const { access_token } = response.data;
            setMessage('Login successful');
            localStorage.setItem('access_token', access_token);
            const decodedToken = JSON.parse(atob(access_token.split('.')[1]));
            setUserId(decodedToken.identity.user_id);
        } catch (error) {
            setMessage(error.response.data.message || 'Invalid credentials');
        }
    };

    return (
        <div className="form-container">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit">Login</button>
            </form>
            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default Login;
