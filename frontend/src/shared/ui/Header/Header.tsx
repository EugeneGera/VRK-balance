import { Gazprom } from "@/shared/assets/icons";
import { ThemePicker} from "@tinkerbells/xenon-ui";
import { Container } from "../Container/Container";
import "./style.scss";
import { Navbar } from "../Navbar/Navbar";
import { Link, useSearchParams } from "react-router";


export const Header = () => {
  const [searchParams] = useSearchParams()
  return (
    <header className="header">
      <Container className="header__content">
        <div className="header__navbar">
          <Link to={{pathname: "/balance_comission", search: searchParams.toString() }}>
          
          <Gazprom />
          </Link>
          <Navbar/>
        </div>
        <div className="header__buttons">
          <ThemePicker />
        </div>
      </Container>
    </header>
  );
};
