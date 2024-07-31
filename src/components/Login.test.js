import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import Login from './Login';

jest.mock('axios');

test('successful login', async () => {
    axios.post.mockResolvedValue({ data: { access_token: 'test_token' } });

    const { getByPlaceholderText, getByText, getByRole } = render(<Login setUserId={() => {}} />);

    fireEvent.change(getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(getByPlaceholderText('Password'), { target: { value: 'password123' } });

    fireEvent.click(getByRole('button', { name: /login/i }));

    await waitFor(() => expect(getByText(/login successful/i)).toBeInTheDocument());
});

test('login error', async () => {
    axios.post.mockRejectedValue({ response: { data: { message: 'Invalid credentials' } } });

    const { getByPlaceholderText, getByText, getByRole } = render(<Login setUserId={() => {}} />);

    fireEvent.change(getByPlaceholderText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(getByPlaceholderText('Password'), { target: { value: 'password123' } });

    fireEvent.click(getByRole('button', { name: /login/i }));

    await waitFor(() => expect(getByText(/invalid credentials/i)).toBeInTheDocument());
});
