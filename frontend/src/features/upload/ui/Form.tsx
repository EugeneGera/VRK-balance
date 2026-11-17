import { Button, notification, Typography } from "@tinkerbells/xenon-ui";
import { Controller, FieldValues, useForm } from "react-hook-form";
import "./style.scss";

import { Alert, DatePicker, Divider, Select, Upload } from "antd";
import { journals } from "../model/consts";
import { BoxIcon } from "@/shared/assets/icons";
import { useUploadApplicationsMutation } from "../api";
import { useEffect, useState } from "react"; // 👈 добавляем useState
import { Spinner } from "@/shared/ui";
import { useAppDispatch } from "@/app/store";
import { setSuccsessUpload } from "@/widgets/filters/models/successUploadSlice";

export const UploadForm = ({
  callbackOnSuccess,
}: {
  callbackOnSuccess?: () => void;
}) => {
  const { handleSubmit, setValue, control, watch, reset } = useForm();
  const dispath = useAppDispatch();
  const [uploadFiles, { isError, isSuccess, isLoading, error, reset: resetMutation }] =
    useUploadApplicationsMutation();

  const [fileList, setFileList] = useState<any[]>([]);

  const onSubmit = (data: FieldValues) => {
    const uploadData = new FormData();
    uploadData.set("file", data.uploadFile);
    uploadData.set("type", data.journals);
    uploadData.set("year", data.year.$y);
    uploadFiles(uploadData);
  };

  const watchFields = watch(["year", "journals"]);
  const watchFile = watch("uploadFile");

  useEffect(() => {
    if (isSuccess) {
      dispath(setSuccsessUpload(true));
      callbackOnSuccess?.();
      
      reset();
      resetMutation();
      setFileList([]);

      notification({
        title: "Файл загружен в систему",
        status: "success",
        position: "bottom-right",
      });
    }
  }, [callbackOnSuccess, dispath, isSuccess, reset, resetMutation]);

  return (
    <form className="upload-form" onSubmit={handleSubmit(onSubmit)}>
      <Typography weight={500} level="heading4">
        Загрузите данные
      </Typography>
      <div className="upload-form__inputs">
        <div className="upload-form__input">
          <Typography className="upload-form__label">Выберите год</Typography>
          <Controller
            rules={{ required: true }}
            control={control}
            name="year"
            render={({ field }) => (
              <DatePicker
                {...field}
                allowClear={false}
                onChange={(value) => setValue("year", value)}
                picker="year"
                format="YYYY"
              />
            )}
          />
        </div>
        <div className="upload-form__input">
          <Typography className="upload-form__label">
            Выберите журнал
          </Typography>
          <Controller
            rules={{ required: true }}
            control={control}
            name="journals"
            render={({ field }) => (
              <Select
                options={journals}
                placeholder="Выберите журнал"
                {...field}
              />
            )}
          />
        </div>
        <Divider />

        <Controller
          rules={{ required: true }}
          control={control}
          name="uploadFile"
          render={({ field }) => (
            <Upload.Dragger
              name={field.name}
              fileList={fileList} // 👈 связываем с состоянием
              onChange={(info) => {
                setFileList(info.fileList); // 👈 обновляем fileList

                if (info.file.status === "removed") {
                  setValue("uploadFile", null);
                } else {
                  // Только если файл добавлен и не в состоянии ошибки/загрузки
                  if (info.file.status === "done" || !info.file.status) {
                    setValue("uploadFile", info.file);
                  }
                }
              }}
              beforeUpload={() => false}
              multiple={false}
              maxCount={1}
              accept=".zip,application/octet-stream, application/zip,application/excel, application/x-zip,application/x-zip-compressed, application/vnd.ms-excel, .xlsx, .xls, .xlsm"
            >
              <BoxIcon />
              <Typography className="upload-form__upload-text" as={"p"}>
                Нажмите на эту область для загрузки файла
              </Typography>
              <Typography className="upload-form__upload-warning" as={"p"}>
                Файлы формата xlsx, xls, zip, xlsm
              </Typography>
            </Upload.Dragger>
          )}
        />
      </div>

      <Button
        disabled={!watchFields[0] || !watchFields[1] || !watchFile || isLoading}
        type="submit"
        className="upload-form__button"
      >
        Отправить {isLoading && <Spinner width="20px" />}
      </Button>
      {
        //@ts-ignore
        isError && error && (
          <Alert message={error?.data?.message} type="error" />
        )
      }
    </form>
  );
};