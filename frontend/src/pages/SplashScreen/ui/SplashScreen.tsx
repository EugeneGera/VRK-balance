

import './style.scss'
import { Tower } from '@/shared/assets/icons';
import { Spinner} from '@/shared/ui';
import { Typography } from '@tinkerbells/xenon-ui';

export const SplashScreen = () => {
  return (
    <div className="splashscreen">
      <div className="splashscreen__content">
        <Tower className="splashscreen__icon" />
        <Typography as="h1" className="splashscreen__title"level="heading3" >
           Баланс распредения товарной продукции
        </Typography>
        <div className="splashscreen__description">
          <Spinner width="14px" />
          <Typography as="p" level="body">Подождите секунду</Typography>
        </div>
      </div>
    </div>
  );
};
