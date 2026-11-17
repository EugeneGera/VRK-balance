import {
  Button,
  CloseOutlined,
  Flex,
  notification,
} from "@tinkerbells/xenon-ui";
import { Col, Input, Row, Typography } from "antd";
import { Controller } from "react-hook-form";
import "./style.scss";
import { useDirectoryForm } from "../../model/useDirectoryForm";

type EditValues = { id: number | string; name: string }[];

export const DirectoryForm = ({
  edits,
  activeDir,
}: {
  edits: EditValues;
  activeDir: string | number;
}) => {
  const {
    handleSubmit,
    onSubmit,
    control,
    getValues,
    resetField,
    isDirty,
    isLoading,
    formValues,
  } = useDirectoryForm(edits, activeDir);

  return (
    <form
      onSubmit={handleSubmit(onSubmit, (errors) => {
        if (Object.keys(errors).length > 0) {
          notification({
            title: "Внимание!",
            status: "warning",
            description: "Изменённые поля не могут быть пустыми.",
          });
        }
      })}
      className="directory-form"
    >
      <Flex vertical>
        <Flex gap={"16px"} vertical className="directory-form__fields">
          {Object.entries(formValues)?.map(([key], index) => (
            <Row gutter={2} align={"middle"} key={index}>
              <Col span={1}>
                <Typography>{index + 1}.</Typography>
              </Col>
              <Col span={23}>
                <Controller
                  rules={{ required: true }}
                  control={control}
                  name={key}
                  key={key}
                  render={({ field }) => (
                    <Input
                      {...field}
                      data-key={key}
                      addonAfter={
                        getValues(key) ==
                        edits.find((i) => i.id === key)?.name ? (
                          " "
                        ) : (
                          <CancelButton
                            onClick={() =>
                              resetField(key, {
                                defaultValue: edits.find((i) => i.id === key),
                              })
                            }
                          />
                        )
                      }
                    />
                  )}
                />
              </Col>
            </Row>
          ))}
        </Flex>
        <Button
          disabled={!isDirty || isLoading}
          className="directory-form__button"
        >
          {isLoading && <span>Сохранение...</span>}
          Сохранить
        </Button>
      </Flex>
    </form>
  );
};

const CancelButton = ({ onClick }: { onClick?: () => void }) => {
  return (
    <CloseOutlined
      onClick={onClick}
      height={15}
      width={15}
      color="var(--xenon-color-icon)"
    />
  );
};
