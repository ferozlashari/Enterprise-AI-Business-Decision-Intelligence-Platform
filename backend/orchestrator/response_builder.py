import json



class ResponseBuilder:


    def build(self,result):


        if not result:

            return {

                "status":"empty"

            }


        if result.get("status")=="error":

            return result



        sections={}


        summary=""


        for key,value in result.items():


            if key in [
                "question",
                "plan",
                "current"
            ]:

                continue



            sections[key]=value



            summary += (

                f"\n\n===== {key.upper()} =====\n"

            )



            if isinstance(value,dict):

                summary += json.dumps(
                    value,
                    indent=2,
                    default=str
                )

            else:

                summary += str(value)



        return {


            "status":"success",


            "summary":summary,


            "details":sections

        }