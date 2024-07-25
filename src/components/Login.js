import React, { useState } from 'react';
import axios from 'axios';

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
            // Decode the token to get the user ID (assumes a standard JWT payload)
            const decodedToken = JSON.parse(atob(access_token.split('.')[1]));
            setUserId(decodedToken.identity.user_id); // Assumes the payload contains user_id
        } catch (error) {
            setMessage('Invalid credentials');
        }
    };

    return (
        <div>
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
            <p>{message}</p>
        </div>
    );
};

export default Login;
