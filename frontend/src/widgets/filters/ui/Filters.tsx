import {
  Button,
  Card,
  Checkbox,
  DatePicker,
  Modal,
  Select,
  Typography,
} from "@tinkerbells/xenon-ui";
import { FC, useEffect, useState } from "react";
import "./style.scss";
import { SavedButton } from "./SavedButton";

import { useDateFilter } from "../models/useDatePicker";
import { useFilters } from "../models/useFilters";
import { UploadForm } from "@/features/upload";
import { useAppDispatch } from "@/app/store";


import { setExpanded } from "@/pages/balance/model/mainTableSlice";
import { setSuccsessUpload } from "../models/successUploadSlice";

export const Filters: FC<{onOpenReport?: () => void}> = ({onOpenReport}) => {
  const {
    isJournalPage,
    selectedFactories,
    selectedCategory,
    selectedProduct,
    isHideZero,
    products,
    factories,
    categories,
    handleProductChange,
    handleFactoryChange,
    handleHideZeroChange,
    handleCategoryChange,
    setSearchParams,
    searchParams, 
    navigate
  } = useFilters();

  const [modalOpen, setModalOpen] = useState(false);
  const dispatch = useAppDispatch();

  useEffect(() => {
   if (isHideZero && isJournalPage) {
      const params = new URLSearchParams(searchParams);
      params.set("hide_zero", "true");
      setSearchParams(params);
      navigate(`?${params.toString()}`);
   } 
  }, [isHideZero, isJournalPage, navigate, searchParams, setSearchParams])

  const printClick: React.MouseEventHandler<HTMLButtonElement> = () => {
    dispatch(setExpanded(true));
    setTimeout(() => {
      window.print();
    }, 100);
  };

  return (
    <Card className="filters-card">
      <div className="filters-wrapper">
        <div className="filters">
          <DateFilter />
          <Typography>Категория</Typography>
          <Select
            className="filters__select"
            placeholder="Выберите категорию"
            allowClear={isJournalPage}
            options={categories.filter((item) => item.value !== "0")}
            value={selectedCategory}
            onChange={handleCategoryChange}
          />
          <Typography>Продукт</Typography>
          <Select
            className="filters__select"
            placeholder="Выберите продукт"
            allowClear
            options={products}
            value={selectedProduct}
            onChange={handleProductChange}
            mode="multiple"
          />
          {/* <Typography>Завод</Typography>
          <Select
            value={selectedFactories}
            mode="multiple"
            allowClear
            className="filters__select"
            placeholder="Выберите вариант"
            options={factories}
            onChange={handleFactoryChange}
          /> */}
         
        </div>
        <div className="journal-btns">
          {isJournalPage ? (
            <>
              <Button
                onClick={() => setModalOpen(true)}
                style={{ width: "155px" }}
              >
                Загрузить данные
              </Button>
              <Checkbox
                id="hide-zero"
                checked={isHideZero}
                name="hide-zero"
                onChange={(e) => handleHideZeroChange(e.target.checked)}
              >
                Cкрыть нулевые значения
              </Checkbox>
              <SavedButton />
            </>
          ) : (
            <>{onOpenReport && <Button color="primary" variant="solid" onClick={onOpenReport}>Подготовить отчёт</Button>}
            <Button onClick={printClick}>Печать </Button></>
          )}
        </div>
      </div>
      <Modal
        className="upload-modal"
        okButtonProps={{ style: { display: "none" } }}
        cancelButtonProps={{ style: { display: "none" } }}
        centered
        open={modalOpen}
        maskClosable={false}
        onCancel={() => setModalOpen(false)}
        destroyOnHidden
      >
        <UploadForm
          callbackOnSuccess={() => {
            setModalOpen(false);
            dispatch(setSuccsessUpload(false));
          }}
        />
      </Modal>
    </Card>
  );
};

const DateFilter = () => {
  const { range, selectedYear, onChangeDate } = useDateFilter();
  return (
    <>
      <Typography>
        {
          //@ts-ignore
          selectedYear.$y
        }
      </Typography>
      <DatePicker
        picker="month"
        format={"MMMM"}
        allowClear={false}
        value={range}
        //@ts-ignore
        onChange={onChangeDate}
        placeholder={"Выберите месяц"}
        className="filters__select"
      />
    </>
  );
};
