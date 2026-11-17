import { FC } from 'react';
import './style.scss'
import { Tower } from '@/shared/assets/icons';
import { Typography } from '@tinkerbells/xenon-ui';

export const ErrorPage: FC = () => {

    return (
        <div className="error-page">
            <div className="error-page__content">
                <Tower className='error-page__icon' withWarning/>
                <Typography as='h1' className='error-page__title' level='heading3'>У вас нет прав доступа к этому проекту</Typography>
                <Typography as="p">Для получения доступа обратитесь в СУУЗ</Typography>
            </div>
        </div>
    );
};