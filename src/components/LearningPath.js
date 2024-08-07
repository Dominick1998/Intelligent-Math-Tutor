import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const LearningPath = ({ userId }) => {
    const { t } = useTranslation();
    const [learningPath, setLearningPath] = useState([]);
    const [newPath, setNewPath] = useState('');

    useEffect(() => {
        const fetchLearningPath = async () => {
            try {
                const response = await axios.get(`http://localhost:5000/learning_path/${userId}`);
                setLearningPath(response.data.problems.split(','));
            } catch (error) {
                console.error('Error fetching learning path', error);
            }
        };

        fetchLearningPath();
    }, [userId]);

    const updateLearningPath = async () => {
        try {
            await axios.post('http://localhost:5000/learning_path', {
                user_id: userId,
                problems: newPath,
            });
            setLearningPath(newPath.split(','));
            setNewPath('');
        } catch (error) {
            console.error('Error updating learning path', error);
        }
    };

    return (
        <div>
            <h2>{t('learning_path')}</h2>
            <ul>
                {learningPath.map((problem, index) => (
                    <li key={index}>{problem}</li>
                ))}
            </ul>
            <textarea
                value={newPath}
                onChange={(e) => setNewPath(e.target.value)}
                placeholder={t('enter_new_path')}
            />
            <button onClick={updateLearningPath}>{t('update_path')}</button>
        </div>
    );
};

export default LearningPath;
