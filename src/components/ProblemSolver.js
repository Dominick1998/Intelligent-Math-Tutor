import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProblemSolver = ({ userId }) => {
    const [problem, setProblem] = useState(null);
    const [solution, setSolution] = useState('');
    const [feedback, setFeedback] = useState('');
    const [hint, setHint] = useState('');

    useEffect(() => {
        const fetchProblem = async () => {
            try {
                const response = await axios.get(`http://localhost:5000/recommend/${userId}`);
                setProblem(response.data);
                setHint(''); // Reset hint
            } catch (error) {
                setFeedback('No problems available');
            }
        };

        fetchProblem();
    }, [userId]);

    const handleHint = () => {
        setHint(problem.feedback); // Display feedback as hint
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        // Simple client-side solution validation
        if (solution === problem.answer) {
            setFeedback('Correct answer! ' + problem.feedback);
            await axios.post('http://localhost:5000/progress', {
                user_id: userId,
                problem_id: problem.problem_id,
                status: 'completed'
            });
            setSolution(''); // Reset solution input
        } else {
            setFeedback('Incorrect answer, try again.');
        }
    };

    return (
        <div>
            {problem ? (
                <div>
                    <h2>Solve the Problem</h2>
                    <p>{problem.question}</p>
                    <button onClick={handleHint}>Get Hint</button>
                    <p>{hint}</p>
                    <form onSubmit={handleSubmit}>
                        <input
                            type="text"
                            placeholder="Your Solution"
                            value={solution}
                            onChange={(e) => setSolution(e.target.value)}
                        />
                        <button type="submit">Submit</button>
                    </form>
                    <p>{feedback}</p>
                </div>
            ) : (
                <p>{feedback}</p>
            )}
        </div>
    );
};

export default ProblemSolver;
