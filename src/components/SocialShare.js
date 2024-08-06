import React from 'react';
import { FacebookShareButton, TwitterShareButton, LinkedinShareButton, FacebookIcon, TwitterIcon, LinkedinIcon } from 'react-share';
import { useTranslation } from 'react-i18next';

const SocialShare = () => {
    const { t } = useTranslation();
    const shareUrl = 'http://localhost:3000';
    const title = t('share_message');

    return (
        <div>
            <h2>{t('share_achievements')}</h2>
            <FacebookShareButton url={shareUrl} quote={title}>
                <FacebookIcon size={32} round />
            </FacebookShareButton>
            <TwitterShareButton url={shareUrl} title={title}>
                <TwitterIcon size={32} round />
            </TwitterShareButton>
            <LinkedinShareButton url={shareUrl} title={title}>
                <LinkedinIcon size={32} round />
            </LinkedinShareButton>
        </div>
    );
};

export default SocialShare;
