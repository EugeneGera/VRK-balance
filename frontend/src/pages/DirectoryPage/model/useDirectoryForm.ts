import { notification } from "@tinkerbells/xenon-ui";
import { useEffect } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import { useUpdateDirectoryFieldsMutation } from "../api";

type EditValues = { id: number | string; name: string }[];
interface FormValues {
  [key: string]: string;
}

export const useDirectoryForm = (
  edits: EditValues,
  activeDir: string | number
) => {
  const {
    handleSubmit,
    control,
    reset,
    getValues,
    resetField,
    formState: { isDirty },
  } = useForm();

  const [updateFields, { isLoading, data: response, error }] =
    useUpdateDirectoryFieldsMutation();

  const formValues = edits.reduce((obj, item) => {
    obj[String(item.id)] = item.name;
    return obj;
  }, {} as FormValues);

  const onSubmit: SubmitHandler<FormValues> = (data) => {
    const formatedData = Object.entries(data).map(([key, value]) => ({
      id: key,
      name: value.trim(),
    }));
    if (!formatedData.some((dict) => dict.name.length === 0)) {
      updateFields({
        id: activeDir,
        fields: {
          directories: formatedData,
        },
      });
    }
  };

  useEffect(() => {
    reset({ ...formValues });
  }, [edits]);

  useEffect(() => {
    if (response) {
      notification({
        title: "Успешно",
        status: "success",
        description: "Изменения сохранены",
      });
    }
  }, [response]);

  useEffect(() => {
    if (error) {
      notification({
        title: "Произошла ошибка",
        status: "error",
        description: JSON.stringify(error),
      });
    }
  }, [error]);

  return {
    handleSubmit,
    onSubmit,
    control,
    reset,
    getValues,
    resetField,
    isDirty,
    isLoading,
    error,
    formValues,
  };
};
