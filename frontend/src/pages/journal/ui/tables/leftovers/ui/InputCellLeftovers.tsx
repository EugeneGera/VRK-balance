import { useAppDispatch, useAppSelector } from "@/app/store";
import { CloseOutlined, Input } from "@tinkerbells/xenon-ui";
import { FC, useState, KeyboardEvent, useEffect } from "react";
import {
  addLeftoversItem,
  deleteLeftoversItem,
  LeftoversItem,
} from "../models/leftoversSlice";
import { setEndEdit } from "@/widgets/filters/models/currentTabSlice";
import "../../table.style.scss";
import { InputNumber } from "antd";

interface InputCellProps {
  data: string;
  rowId: number;
  fieldName: keyof LeftoversItem;
}

export const InputCellLeftovers: FC<InputCellProps> = ({
  data,
  rowId,
  fieldName,
}) => {
  const [value, setValue] = useState<string | null>(data);
  const [isEdited, setIsEdited] = useState<boolean>(false);

  const dispath = useAppDispatch();
  const endEdit = useAppSelector((state) => state.currentTab.endEdit);

  const handleChangeTextInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);

    if (e.target.value !== String(data)) {
      setIsEdited(true);
    } else {
      setIsEdited(false);
    }
  };

  const handleChangeNumInput = (val: string | null) => {
    setValue(val);

    if (val !== String(data)) {
      setIsEdited(true);
    } else {
      setIsEdited(false);
    }
  };

  const formatter = (value: string | number | undefined) => {
    if (!value) return "";
    return `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  };

  const parser = (value: string | undefined) => {
    return value ? value.replace(/\s/g, "") : "";
  };

  const handleBlur = () => {
    if (isEdited) {
      dispath(setEndEdit(false));
      dispath(
        addLeftoversItem({
          id: rowId,
          [fieldName]: fieldName === "remark" ? value : Number(value),
        })
      );
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (isEdited) {
        dispath(setEndEdit(false));
        dispath(
          addLeftoversItem({
            id: rowId,
            [fieldName]: fieldName === "remark" ? value : Number(value),
          })
        );
      }
    }
  };

  const removeButton = (): React.CSSProperties => {
    let result: { cursor: string; display?: string } = { cursor: "pointer" };
    if (!isEdited) {
      result = { ...result, display: "none" };
    }
    return result;
  };

  useEffect(() => {
    if (endEdit) {
      setIsEdited(false);
    }
  }, [endEdit]);

  const handleClick = () => {
    setValue(data);
    setIsEdited(false);

    dispath(
      deleteLeftoversItem({
        id: rowId,
        fieldsToDelete: [fieldName],
      })
    );
  };

  if (fieldName === "remark") {
    return (
      <Input
        className="input"
        type={fieldName === "remark" ? "text" : "number"}
        addonAfter={
          <div onClick={handleClick} style={{ display: "flex" }}>
            <CloseOutlined
              height={15}
              width={15}
              color="var(--xenon-color-icon)"
              style={removeButton()}
            />
          </div>
        }
        value={value ?? ""}
        onChange={handleChangeTextInput}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
      />
    );
  }

  return (
    <InputNumber
      className="input"
      addonAfter={
        <div onClick={handleClick} style={{ display: "flex" }}>
          <CloseOutlined
            height={15}
            width={15}
            color="var(--xenon-color-icon)"
            style={removeButton()}
          />
        </div>
      }
      formatter={formatter}
      parser={parser}
      value={value}
      onChange={handleChangeNumInput}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
    />
  );
};
