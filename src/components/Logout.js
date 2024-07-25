import React from 'react';
import axios from 'axios';

const Logout = ({ setUserId }) => {
    const handleLogout = async () => {
        const token = localStorage.getItem('access_token');
        await axios.post('http://localhost:5000/logout', {}, {
            headers: { Authorization: `Bearer ${token}` }
        });
        localStorage.removeItem('access_token');
        setUserId(null);
    };

    return (
        <button onClick={handleLogout}>Logout</button>
    );
};

export default Logout;
