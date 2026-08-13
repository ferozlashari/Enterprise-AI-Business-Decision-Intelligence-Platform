import api from "../../api/axios";





export const fetchInventory = async()=>{


    const response =
    await api.get(

        "/inventory/all"

    );


    return response.data;


};





export const fetchInventoryPrediction = async()=>{


    const response =
    await api.get(

        "/inventory/predict"

    );


    return response.data;


};
