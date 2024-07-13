import React, { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import ProblemSolver from './components/ProblemSolver';
import Progress from './components/Progress';

const App = () => {
    const [userId, setUserId] = useState(null);

    return (
        <div>
            {!userId ? (
                <div>
                    <Register />
                    <Login setUserId={setUserId} />
                </div>
            ) : (
                <div>
                    <ProblemSolver userId={userId} />
                    <Progress userId={userId} />
                </div>
            )}
        </div>
    );
};

export default App;
