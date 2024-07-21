import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Register from '../Register';

test('renders Register component', () => {
    render(<Register />);
    const heading = screen.getByText(/Register/i);
    expect(heading).toBeInTheDocument();
});

test('handles registration form submission', () => {
    render(<Register />);
    fireEvent.change(screen.getByPlaceholderText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByText('Register'));
    expect(screen.getByText(/Error registering user/i)).toBeInTheDocument();
});
