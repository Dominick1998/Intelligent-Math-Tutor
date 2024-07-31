import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import Register from './Register';

jest.mock('axios');

test('successful registration', async () => {
    axios.post.mockResolvedValue({ data: { message: 'User registered successfully' } });

    const { getByPlaceholderText, getByText, getByRole } = render(<Register />);

    fireEvent.change(getByPlaceholderText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(getByPlaceholderText('Password'), { target: { value: 'password123' } });

    fireEvent.click(getByRole('button', { name: /register/i }));

    await waitFor(() => expect(getByText(/user registered successfully/i)).toBeInTheDocument());
});

test('registration error', async () => {
    axios.post.mockRejectedValue({ response: { data: { message: 'Error registering user' } } });

    const { getByPlaceholderText, getByText, getByRole } = render(<Register />);

    fireEvent.change(getByPlaceholderText('Username'), { target: { value: 'testuser' } });
    fireEvent.change(getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(getByPlaceholderText('Password'), { target: { value: 'password123' } });

    fireEvent.click(getByRole('button', { name: /register/i }));

    await waitFor(() => expect(getByText(/error registering user/i)).toBeInTheDocument());
});
