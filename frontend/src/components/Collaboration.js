import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import './Collaboration.css'; // Assuming you want to add some basic styles

const socket = io.connect('http://localhost:5000'); // Update with your backend URL if different

const Collaboration = () => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const canvasRef = useRef(null);
    const contextRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);

    useEffect(() => {
        // Setup event listeners for incoming messages
        socket.on('response', (data) => {
            setMessages((prevMessages) => [...prevMessages, data.message]);
        });

        // Setup event listeners for drawing
        socket.on('draw', (data) => {
            const { x0, y0, x1, y1 } = data;
            drawLine(x0, y0, x1, y1);
        });

        // Setup the canvas
        const canvas = canvasRef.current;
        canvas.width = window.innerWidth * 0.8;
        canvas.height = window.innerHeight * 0.6;
        canvas.style.width = `${window.innerWidth * 0.8}px`;
        canvas.style.height = `${window.innerHeight * 0.6}px`;

        const context = canvas.getContext('2d');
        context.strokeStyle = 'black';
        context.lineWidth = 5;
        context.lineCap = 'round';
        contextRef.current = context;
    }, []);

    const handleMessageSubmit = (e) => {
        e.preventDefault();
        socket.emit('message', { message });
        setMessage('');
    };

    const drawLine = (x0, y0, x1, y1) => {
        contextRef.current.beginPath();
        contextRef.current.moveTo(x0, y0);
        contextRef.current.lineTo(x1, y1);
        contextRef.current.stroke();
        contextRef.current.closePath();
    };

    const handleMouseDown = (e) => {
        const { offsetX, offsetY } = e.nativeEvent;
        setIsDrawing(true);
        contextRef.current.beginPath();
        contextRef.current.moveTo(offsetX, offsetY);
    };

    const handleMouseMove = (e) => {
        if (!isDrawing) return;
        const { offsetX, offsetY } = e.nativeEvent;
        drawLine(contextRef.current.lastX, contextRef.current.lastY, offsetX, offsetY);
        contextRef.current.lastX = offsetX;
        contextRef.current.lastY = offsetY;

        socket.emit('draw', {
            x0: contextRef.current.lastX,
            y0: contextRef.current.lastY,
            x1: offsetX,
            y1: offsetY,
        });
    };

    const handleMouseUp = () => {
        setIsDrawing(false);
    };

    return (
        <div className="collaboration-container">
            <div className="messages">
                <ul>
                    {messages.map((msg, index) => (
                        <li key={index}>{msg}</li>
                    ))}
                </ul>
            </div>
            <form onSubmit={handleMessageSubmit}>
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message"
                />
                <button type="submit">Send</button>
            </form>
            <canvas
                ref={canvasRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                className="whiteboard"
            ></canvas>
        </div>
    );
};

export default Collaboration;
