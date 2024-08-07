import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';

const Tutorials = () => {
    const { t } = useTranslation();
    const [tutorials, setTutorials] = useState([]);
    const [selectedTutorial, setSelectedTutorial] = useState(null);

    useEffect(() => {
        const fetchTutorials = async () => {
            try {
                const response = await axios.get('http://localhost:5000/tutorials');
                setTutorials(response.data);
            } catch (error) {
                console.error('Error fetching tutorials', error);
            }
        };

        fetchTutorials();
    }, []);

    const selectTutorial = async (id) => {
        try {
            const response = await axios.get(`http://localhost:5000/tutorials/${id}`);
            setSelectedTutorial(response.data);
        } catch (error) {
            console.error('Error fetching tutorial', error);
        }
    };

    return (
        <div>
            <h2>{t('tutorials')}</h2>
            <ul>
                {tutorials.map((tutorial) => (
                    <li key={tutorial.id} onClick={() => selectTutorial(tutorial.id)}>
                        {tutorial.title}
                    </li>
                ))}
            </ul>
            {selectedTutorial && (
                <div>
                    <h3>{selectedTutorial.title}</h3>
                    <p>{selectedTutorial.content}</p>
                </div>
            )}
        </div>
    );
};

export default Tutorials;
