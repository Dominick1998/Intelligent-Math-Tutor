import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Login from '../Login';

test('renders Login component', () => {
    render(<Login />);
    const heading = screen.getByText(/Login/i);
    expect(heading).toBeInTheDocument();
});

test('handles login form submission', () => {
    render(<Login setUserId={() => {}} />);
    fireEvent.change(screen.getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password123' } });
    fireEvent.click(screen.getByText('Login'));
    expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
});
