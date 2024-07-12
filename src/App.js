import React, { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import ProblemSolver from './components/ProblemSolver';

const App = () => {
    const [userId, setUserId] = useState(null);

    return (
        <div>
            {!userId ? (
                <div>
                    <Register />
                    <Login />
                </div>
            ) : (
                <ProblemSolver userId={userId} />
            )}
        </div>
    );
};

export default App;
