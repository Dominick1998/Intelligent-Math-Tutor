import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

const CollaborationRoom = ({ username, room }) => {
    const { t } = useTranslation();
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        socket.emit('join', { username, room });

        socket.on('message', (message) => {
            setMessages((msgs) => [...msgs, message]);
        });

        return () => {
            socket.emit('leave', { username, room });
            socket.off();
        };
    }, [username, room]);

    const sendMessage = (e) => {
        e.preventDefault();
        if (message) {
            socket.emit('message', { room, message });
            setMessage('');
        }
    };

    return (
        <div>
            <h2>{t('collaboration_room')} - {room}</h2>
            <div>
                {messages.map((msg, index) => (
                    <p key={index}>{msg}</p>
                ))}
            </div>
            <form onSubmit={sendMessage}>
                <input
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder={t('enter_message')}
                />
                <button type="submit">{t('send')}</button>
            </form>
        </div>
    );
};

export default CollaborationRoom;
