import React from 'react';
import { render, screen } from '@testing-library/react';
import ProblemSolver from '../ProblemSolver';

test('renders ProblemSolver component', () => {
    render(<ProblemSolver userId={1} />);
    const heading = screen.getByText(/Solve the Problem/i);
    expect(heading).toBeInTheDocument();
});
