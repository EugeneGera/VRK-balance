import { useAppDispatch } from "@/app/store";
import { useGetAllCategoriesQuery } from "@/entities/categories/api";
import { useGetAllFactoriesQuery } from "@/entities/factories/api";
import { useGetAllProductsQuery } from "@/entities/products/api";
import { useState, useEffect, useCallback } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router";

export const useFilters = () => {
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [isJournalPage, setIsJournalPage] = useState<boolean>(false);
  const [isMainPage, setIsMainPage] = useState<boolean>(false);
  const [selectedProduct, setSelectedProduct] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedFactories, setSelectedFactories] = useState<string[]>([]);
  const [isHideZero, setIsHideZero] = useState<boolean>(true);

  const { data: products } = useGetAllProductsQuery(selectedCategory);
  const { data: categories } = useGetAllCategoriesQuery();

  const { data: factories } = useGetAllFactoriesQuery(searchParams.toString(), {
    skip: searchParams.toString() === "",
  });

  const dispatch = useAppDispatch();
  const changeSelectFilter = useCallback(
    (key: string, value: string | string[]) => {
      const newSearchParams = new URLSearchParams(location.search);

      if (Array.isArray(value) && value.length > 0) {
        newSearchParams.set(key, value.join(","));
      } else if (value && !Array.isArray(value)) {
        newSearchParams.set(key, value);
      } else {
        newSearchParams.delete(key);
      }

      navigate(`?${newSearchParams.toString()}`);
    },
    [location.search, navigate]
  );
  const handleProductChange = (value: string[]) => {
    const newSearchParams = new URLSearchParams(location.search);

    if (value.length > 0) {
      newSearchParams.set("product", value.join(","));
    } else {
      newSearchParams.delete("product");
    }

    newSearchParams.delete("basises");

    setSelectedProduct(value);
    setSelectedFactories([]);

    navigate(`?${newSearchParams.toString()}`);
  };

  const handleCategoryChange = (value: string | undefined) => {
    const newSearchParams = new URLSearchParams(location.search);

    if (value) {
      if (value.length > 0) {
        newSearchParams.set("category_product", value);
      }
    } else {
      newSearchParams.delete("category_product");
    }

    newSearchParams.delete("product");
    newSearchParams.delete("basises");

    setSelectedCategory(value ?? null);
    setSelectedProduct([]);
    setSelectedFactories([]);

    navigate(`?${newSearchParams.toString()}`);
  };

  const handleFactoryChange = (value: string[]) => {
    changeSelectFilter("basises", value);
    setSelectedFactories(value);
  };

  const handleHideZeroChange = (checked: boolean) => {
    setIsHideZero(checked);
    if (checked) {
      changeSelectFilter("hide_zero", "true");
    } else {
      changeSelectFilter("hide_zero", "");
    }
  };

  useEffect(() => {
    if (categories?.category_product) {
      const isJournal = location.pathname.includes("business-journal");
      const searchCategory = searchParams.get("category_product");
      const defaultCategory = searchCategory
        ? searchCategory
        : isJournal
          ? null
          : categories.category_product.find((item) => item.value !== "0")?.value ?? null;
      setSelectedCategory(defaultCategory);
      if (defaultCategory && defaultCategory !== searchCategory) {
        const params = new URLSearchParams(searchParams);
        params.set("category_product", defaultCategory);
        setSearchParams(params, { replace: true });
      }
    }
  }, [location.pathname, categories, searchParams, setSearchParams, dispatch]);

  useEffect(() => {
    setIsJournalPage(location.pathname.includes("business-journal"));
    setIsMainPage(
      !isJournalPage && !location.pathname.includes("table-balance")
    );
    const searchFactories = searchParams.get("basises");
    setSelectedFactories(searchFactories?.split(",") || []);
    setSelectedProduct(searchParams.get("product")?.split(",") || []);
  }, [isJournalPage, location.pathname, searchParams]);

  return {
    isJournalPage,
    isMainPage,
    selectedProduct,
    selectedCategory,
    selectedFactories,
    isHideZero,
    categories: categories?.category_product || [],
    products: products?.products || [],
    factories: factories?.factories || [],
    handleProductChange,
    handleFactoryChange,
    handleHideZeroChange,
    handleCategoryChange,
    searchParams,
    setSearchParams,
    navigate
  };
};
