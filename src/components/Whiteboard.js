import React, { useRef, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import io from 'socket.io-client';

const socket = io('http://localhost:5000');

const Whiteboard = ({ username, room }) => {
    const { t } = useTranslation();
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);

    useEffect(() => {
        socket.emit('join', { username, room });

        socket.on('draw', (data) => {
            const canvas = canvasRef.current;
            const context = canvas.getContext('2d');
            const { x0, y0, x1, y1 } = data;
            drawLine(context, x0, y0, x1, y1);
        });

        return () => {
            socket.emit('leave', { username, room });
            socket.off();
        };
    }, [username, room]);

    const startDrawing = ({ nativeEvent }) => {
        const { offsetX, offsetY } = nativeEvent;
        setIsDrawing(true);
        draw(offsetX, offsetY);
    };

    const finishDrawing = () => {
        setIsDrawing(false);
        contextRef.current.beginPath();
    };

    const draw = (x, y) => {
        if (!isDrawing) return;

        const context = canvasRef.current.getContext('2d');
        context.lineWidth = 5;
        context.lineCap = 'round';
        context.lineTo(x, y);
        context.stroke();
        context.beginPath();
        context.moveTo(x, y);

        socket.emit('draw', {
            room,
            drawData: { x0: x, y0: y, x1: x, y1: y },
        });
    };

    return (
        <div>
            <h2>{t('whiteboard')}</h2>
            <canvas
                ref={canvasRef}
                onMouseDown={startDrawing}
                onMouseUp={finishDrawing}
                onMouseMove={({ nativeEvent }) => draw(nativeEvent.offsetX, nativeEvent.offsetY)}
                width={800}
                height={600}
                style={{ border: '1px solid black' }}
            ></canvas>
        </div>
    );
};

export default Whiteboard;
