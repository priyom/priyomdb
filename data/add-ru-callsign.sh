#!/bin/bash
sed -r "/SELECT @transmissionId:=/s/$/\nINSERT INTO \`foreignSupplement\` (LocalID, FieldName, ForeignText, LangCode) VALUES (@transmissionId, 'transmissions.Callsign', @callsignRu, 'ru');/;"
