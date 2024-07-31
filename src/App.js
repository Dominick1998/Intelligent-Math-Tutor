import React, { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import ProblemSolver from './components/ProblemSolver';
import Progress from './components/Progress';
import Logout from './components/Logout';
import Profile from './components/Profile';
import Dashboard from './components/Dashboard';
import Feedback from './components/Feedback';
import './App.css';

const App = () => {
    const [userId, setUserId] = useState(null);

    return (
        <div className="App">
            {!userId ? (
                <div>
                    <Register />
                    <Login setUserId={setUserId} />
                </div>
            ) : (
                <div>
                    <Logout setUserId={setUserId} />
                    <Dashboard />
                    <Profile />
                    <ProblemSolver userId={userId} />
                    <Progress userId={userId} />
                    <Feedback />
                </div>
            )}
        </div>
    );
};

export default App;
