import React, { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import ProblemSolver from './components/ProblemSolver';
import Progress from './components/Progress';
import Logout from './components/Logout';
import Profile from './components/Profile';
import Dashboard from './components/Dashboard';
import Feedback from './components/Feedback';
import Analytics from './components/Analytics';
import Badges from './components/Badges';
import Notifications from './components/Notifications';
import SocialShare from './components/SocialShare';
import Tutorials from './components/Tutorials';
import LearningPath from './components/LearningPath';
import AdminPanel from './components/AdminPanel';
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
                    <Analytics />
                    <Badges />
                    <Notifications />
                    <SocialShare />
                    <Tutorials />
                    <LearningPath userId={userId} />
                    <AdminPanel />
                </div>
            )}
        </div>
    );
};

export default App;
