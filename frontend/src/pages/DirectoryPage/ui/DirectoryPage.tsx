import { Header } from "@/shared/ui";
import { Container } from "@/shared/ui/Container/Container";
import {
  Card,
  Flex,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Typography,
} from "@tinkerbells/xenon-ui";
import { FC, useEffect, useState } from "react";
import "./style.scss";
import { DirsKeys } from "../model/consts";
import { DirectoryForm } from "./components/Form";
import { useGetDirectoriesQuery, useLazyGetDirectoryInfoQuery } from "../api";
import { useLocation, useNavigate } from "react-router";

export const DirectoryPage: FC = () => {
  const [activeDir, setActiveDir] = useState<DirsKeys | null>(null);
  const { data: directories } = useGetDirectoriesQuery();
  const [getDirInfo, { data: directoryFields }] =
    useLazyGetDirectoryInfoQuery();
  const location = useLocation();
  const navigate = useNavigate();

  const setActivaData = (key: DirsKeys | null) => {
    if (key) {
      setActiveDir(key);
    }
  };

  useEffect(() => {
    navigate(location.pathname);
  }, [location.pathname, navigate]);

  useEffect(() => {
    if (activeDir) {
      getDirInfo(activeDir);
    }
  }, [activeDir, getDirInfo]);

  return (
    <>
      <Header />
      <Container>
        <Flex className="directories-container" gap={"24px"}>
          <Card className="directories-card" title="Справочники">
            <Table className="directories-table" size="sm">
              <TableHeader>
                <TableRow>
                  <TableHead>№</TableHead>
                  <TableHead>Название справочника</TableHead>
                  <TableHead>Количество значений</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {directories?.directories &&
                  directories.directories.map((directory, index) => (
                    <TableRow
                      key={directory.table_id}
                      className={`${activeDir === directory.table_id ? "directories-table__row_selected" : ""}`}
                      onClick={() => setActivaData(directory.table_id)}
                    >
                      <TableCell align="center">{index + 1}</TableCell>
                      <TableCell>{directory.table_name}</TableCell>
                      <TableCell align="center">
                        {directory.fields_count}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </Card>
          <Card className="directories-card__edit" title="Редактор справочника">
            <Flex vertical>
              {directoryFields && activeDir ? (
                <>
                  <Card className="directories-card__directory">
                    <Flex vertical align="center">
                      <Typography className="directories-card__subtitle">
                        Выбран справочник{" "}
                      </Typography>
                      <Typography level="heading5" weight={600}>
                        {directories?.directories?.find(
                          (i) => i.table_id === activeDir
                        )?.table_name || ""}
                      </Typography>
                    </Flex>
                  </Card>
                  <DirectoryForm
                    edits={directoryFields.fields}
                    activeDir={activeDir}
                  />
                </>
              ) : (
                <Typography className="directories-card__warning">
                  Выберите справочник
                </Typography>
              )}
            </Flex>
          </Card>
        </Flex>
      </Container>
    </>
  );
};
