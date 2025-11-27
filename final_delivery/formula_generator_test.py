{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "65b1a2d9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Не удалось спарсить лист: Обзор экспорта\n",
      "Не удалось спарсить лист: Landsat-12345 MSS\n",
      "Не удалось спарсить лист: Ресурс-П ГСА\n"
     ]
    }
   ],
   "source": [
    "from formula_generator import convert_formula, parse_satellite_bands_table\n",
    "import pandas as pd\n",
    "\n",
    "sat = parse_satellite_bands_table(\"specification/Спутники.xlsx\")\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "d848fe03",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'SR_B8/SR_B8'"
      ]
     },
     "execution_count": 3,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "f = \"[630:690]/[520:600]\"\n",
    "\n",
    "convert_formula(f, sat['LANDSAT-89 OLITIRS'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "fa055f0f",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": ".venv",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
